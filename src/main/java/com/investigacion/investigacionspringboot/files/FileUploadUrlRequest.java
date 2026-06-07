package com.investigacion.investigacionspringboot.files;

public record FileUploadUrlRequest(
        String fileName,
        String contentType
) {
}
