package com.investigacion.investigacionspringboot.files;

import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@Service
public class FileStorageService {

    private final FileStorageProperties properties;
    private final RestClient restClient;

    public FileStorageService(FileStorageProperties properties, RestClient.Builder restClientBuilder) {
        this.properties = properties;
        this.restClient = restClientBuilder.baseUrl(properties.baseUrl()).build();
    }

    public FileUploadResponse uploadFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new FileStorageException("Debes enviar un archivo");
        }

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", toResource(file));

        Map<String, Object> response = callUploadApi(body);
        String fileId = getStringValue(response, "fileId", "id");

        if (fileId == null || fileId.isBlank()) {
            throw new FileStorageException("La API de archivos no devolvio un ID valido");
        }

        return new FileUploadResponse(fileId);
    }

    public FileDownloadResponse getDownloadUrl(String fileId) {
        if (fileId == null || fileId.isBlank()) {
            throw new FileStorageException("Debes enviar el ID del archivo");
        }

        Map<String, Object> response = callDownloadApi(fileId);
        String downloadUrl = getStringValue(response, "downloadUrl", "url");

        if (downloadUrl == null || downloadUrl.isBlank()) {
            throw new FileStorageException("La API de archivos no devolvio una URL valida");
        }

        return new FileDownloadResponse(fileId, downloadUrl);
    }

    private ByteArrayResource toResource(MultipartFile file) {
        try {
            return new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename();
                }
            };
        } catch (IOException exception) {
            throw new FileStorageException("No se pudo leer el archivo", exception);
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> callUploadApi(MultiValueMap<String, Object> body) {
        try {
            return restClient.post()
                    .uri(properties.uploadPath())
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .body(Map.class);
        } catch (RestClientException exception) {
            throw new FileStorageException("No se pudo subir el archivo a la API externa", exception);
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

    private String getStringValue(Map<String, Object> response, String firstKey, String secondKey) {
        if (response == null) {
            return null;
        }

        Object value = response.get(firstKey);
        if (value == null) {
            value = response.get(secondKey);
        }

        return value == null ? null : value.toString();
    }
}
