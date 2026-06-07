package com.investigacion.investigacionspringboot.files;

import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.HashMap;
import java.util.Map;

@Service
public class FileStorageService {

    private final FileStorageProperties properties;
    private final RestClient restClient;

    public FileStorageService(FileStorageProperties properties, RestClient.Builder restClientBuilder) {
        this.properties = properties;
        this.restClient = restClientBuilder.baseUrl(properties.baseUrl()).build();
    }

    public String requestUploadUrl(Long userId, FileUploadUrlRequest request) {
        Map<String, Object> body = new HashMap<>();
        body.put("clientId", userId);

        if (request != null) {
            body.put("fileName", request.fileName());
            body.put("contentType", request.contentType());
        }

        Map<String, Object> response = callUploadUrlApi(body);
        String uploadUrl = getStringValue(response, "uploadUrl", "url", "location");

        if (uploadUrl == null || uploadUrl.isBlank()) {
            throw new FileStorageException("La API de archivos no devolvio una URL de subida valida");
        }

        return uploadUrl;
    }

    public FileDownloadResponse getDownloadUrl(String fileId) {
        if (fileId == null || fileId.isBlank()) {
            throw new FileStorageException("Debes enviar el ID del archivo");
        }

        Map<String, Object> response = callDownloadApi(fileId);
        String downloadUrl = getStringValue(response, "downloadUrl", "url", "location");

        if (downloadUrl == null || downloadUrl.isBlank()) {
            throw new FileStorageException("La API de archivos no devolvio una URL valida");
        }

        return new FileDownloadResponse(fileId, downloadUrl);
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> callUploadUrlApi(Map<String, Object> body) {
        try {
            return restClient.post()
                    .uri(properties.uploadUrlPath())
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(body)
                    .retrieve()
                    .body(Map.class);
        } catch (RestClientException exception) {
            throw new FileStorageException("No se pudo solicitar la URL de subida a la API externa", exception);
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> callDownloadApi(String fileId) {
        try {
            return restClient.get()
                    .uri(properties.downloadUrlPath(), Map.of("fileId", fileId))
                    .retrieve()
                    .body(Map.class);
        } catch (RestClientException exception) {
            throw new FileStorageException("No se pudo consultar el archivo en la API externa", exception);
        }
    }

    private String getStringValue(Map<String, Object> response, String... keys) {
        if (response == null) {
            return null;
        }

        for (String key : keys) {
            Object value = response.get(key);
            if (value != null) {
                return value.toString();
            }
        }

        return null;
    }
}
