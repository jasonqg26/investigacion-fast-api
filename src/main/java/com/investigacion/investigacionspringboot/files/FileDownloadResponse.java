package com.investigacion.investigacionspringboot.files;

public record FileDownloadResponse(
        String fileId,
        String downloadUrl
) {
}
