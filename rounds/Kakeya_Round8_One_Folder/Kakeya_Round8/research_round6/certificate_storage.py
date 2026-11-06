"""Lossless portable storage for large mathematical certificates.

Logical paths in receipts remain input.cnf, proof.drat, or proof.lrat. If a
logical file is absent, its sibling PATH.xz supplies exactly the same bytes.
Readers verify the logical SHA256 before using those bytes. No proof content
or acceptance rule is changed by compression.
"""
from contextlib import contextmanager
from pathlib import Path
import hashlib
import errno
import lzma
import os
import shutil
import tempfile

BLOCK = 1024 * 1024


def open_logical(path, *, prefer_compressed=False):
    path = Path(path)
    compressed = Path(str(path) + '.xz')
    if prefer_compressed and compressed.is_file():
        return lzma.open(compressed, 'rb')
    if path.is_file():
        return path.open('rb')
    if compressed.is_file():
        return lzma.open(compressed, 'rb')
    raise FileNotFoundError(str(path) + ' (and its .xz sibling)')


def logical_sha(path, *, prefer_compressed=False):
    digest = hashlib.sha256()
    with open_logical(path, prefer_compressed=prefer_compressed) as stream:
        for block in iter(lambda: stream.read(BLOCK), b''):
            digest.update(block)
    return digest.hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(BLOCK), b''):
            digest.update(block)
    return digest.hexdigest()


@contextmanager
def materialized(path, expected_sha256, directory=None, *, prefer_compressed=False):
    """Yield a verified plain file, temporarily decompressing when necessary."""
    path = Path(path)
    compressed = Path(str(path) + '.xz')
    if path.is_file() and not (prefer_compressed and compressed.is_file()):
        if file_sha(path) != expected_sha256:
            raise ValueError('Changed certificate bytes: ' + str(path))
        yield path
        return
    if not compressed.is_file():
        raise FileNotFoundError(str(compressed))
    with tempfile.TemporaryDirectory(prefix='kakeya_certificate_', dir=directory) as temporary:
        output = Path(temporary) / path.name
        digest = hashlib.sha256()
        with lzma.open(compressed, 'rb') as source, output.open('wb') as target:
            for block in iter(lambda: source.read(BLOCK), b''):
                digest.update(block)
                target.write(block)
        if digest.hexdigest() != expected_sha256:
            raise ValueError('Changed decompressed certificate bytes: ' + str(compressed))
        yield output


def compress_verified(path, expected_sha256, *, preset=3, remove_raw=False):
    """Compress atomically; remove a generated raw file only after round-trip verification."""
    path = Path(path)
    compressed = Path(str(path) + '.xz')
    if not path.is_file():
        if not compressed.is_file() or logical_sha(path) != expected_sha256:
            raise ValueError('Missing or changed certificate: ' + str(path))
        return {'logical_path': str(path), 'compressed_path': str(compressed),
                'raw_sha256': expected_sha256, 'xz_sha256': file_sha(compressed),
                'xz_bytes': compressed.stat().st_size, 'raw_present': False}
    raw_bytes = path.stat().st_size
    if file_sha(path) != expected_sha256:
        raise ValueError('Refusing to compress changed certificate: ' + str(path))
    if compressed.is_file():
        digest = hashlib.sha256()
        with lzma.open(compressed, 'rb') as source:
            for block in iter(lambda: source.read(BLOCK), b''):
                digest.update(block)
        if digest.hexdigest() != expected_sha256:
            raise ValueError('Existing compressed certificate differs: ' + str(compressed))
    else:
        # Keep a live compression stream outside the shared workspace. Only
        # the completed, verified immutable result is published there.
        handle = tempfile.NamedTemporaryFile(prefix='kakeya_xz_', suffix='.xz', delete=False)
        temporary = Path(handle.name)
        handle.close()
        try:
            with path.open('rb') as source, lzma.open(temporary, 'wb', preset=preset) as target:
                for block in iter(lambda: source.read(BLOCK), b''):
                    target.write(block)
            digest = hashlib.sha256()
            with lzma.open(temporary, 'rb') as source:
                for block in iter(lambda: source.read(BLOCK), b''):
                    digest.update(block)
            if digest.hexdigest() != expected_sha256:
                raise ValueError('Lossless compression check failed: ' + str(path))
            try:
                os.replace(temporary, compressed)
            except OSError as error:
                if error.errno != errno.EXDEV:
                    raise
                # Some mounted workspaces reject cross-directory rename even
                # when stat reports the same device. Copy a completed file,
                # verify it, and rename within the destination directory.
                handle = tempfile.NamedTemporaryFile(prefix='kakeya_publish_', suffix='.xz',
                                                      dir=compressed.parent, delete=False)
                publication = Path(handle.name)
                handle.close()
                try:
                    shutil.copyfile(temporary, publication)
                    if file_sha(publication) != file_sha(temporary):
                        raise ValueError('Compressed publication copy changed')
                    os.replace(publication, compressed)
                finally:
                    publication.unlink(missing_ok=True)
        finally:
            temporary.unlink(missing_ok=True)
    # Recheck a raw source immediately before removing it.
    if remove_raw:
        if file_sha(path) != expected_sha256:
            raise ValueError('Certificate changed while compressing: ' + str(path))
        path.unlink()
    return {'logical_path': str(path), 'compressed_path': str(compressed),
            'raw_sha256': expected_sha256, 'raw_bytes': raw_bytes,
            'xz_sha256': file_sha(compressed), 'xz_bytes': compressed.stat().st_size,
            'raw_present': path.exists(), 'compression': 'xz', 'preset': preset,
            'round_trip_sha256': expected_sha256}
