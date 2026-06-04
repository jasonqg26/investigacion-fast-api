package com.investigacion.investigacionspringboot.files;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/protected/files")
public class FileController {

    private final FileStorageService fileStorageService;

    public FileController(FileStorageService fileStorageService) {
        this.fileStorageService = fileStorageService;
    }

    @PostMapping
    public ResponseEntity<FileUploadResponse> uploadFile(@RequestParam("file") MultipartFile file) {
        return ResponseEntity.ok(fileStorageService.uploadFile(file));
    }

    @GetMapping("/{fileId}")
    public ResponseEntity<FileDownloadResponse> getDownloadUrl(@PathVariable String fileId) {
        return ResponseEntity.ok(fileStorageService.getDownloadUrl(fileId));
    }
}
