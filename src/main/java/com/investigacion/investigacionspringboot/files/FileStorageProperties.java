package com.investigacion.investigacionspringboot.files;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "file-storage")
public record FileStorageProperties(
        String baseUrl,
        String uploadPath,
        String downloadUrlPath
) {
}
