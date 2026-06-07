package com.investigacion.investigacionspringboot.files;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestAttribute;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;

@RestController
@RequestMapping("/api/protected/files")
public class FileController {

    private final FileStorageService fileStorageService;

    public FileController(FileStorageService fileStorageService) {
        this.fileStorageService = fileStorageService;
    }

    @PostMapping({"", "/upload"})
    public ResponseEntity<Void> requestUploadUrl(
            @RequestAttribute("userId") Long userId,
            @RequestBody(required = false) FileUploadUrlRequest request
    ) {
        String uploadUrl = fileStorageService.requestUploadUrl(userId, request);

        return ResponseEntity.status(HttpStatus.FOUND)
                .location(URI.create(uploadUrl))
                .build();
    }

    @GetMapping("/{fileId}")
    public ResponseEntity<FileDownloadResponse> getDownloadUrl(@PathVariable String fileId) {
        return ResponseEntity.ok(fileStorageService.getDownloadUrl(fileId));
    }
}
