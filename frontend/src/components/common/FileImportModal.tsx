import React, { useState, useRef } from 'react';
import {
  Modal,
  Box,
  Typography,
  Button,
  CircularProgress,
  Alert,
  AlertTitle,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';

interface ImportError {
  row: number;
  field: string;
  message: string;
}

interface BillImport {
  month: string;
  day_of_month: number;
  bill_name: string;
  amount: number;
  account_id: number;
  auto_pay?: boolean;
  splits?: Array<{
    account_id: number;
    amount: number;
  }>;
}

interface IncomeImport {
  date: string;
  source: string;
  amount: number;
  deposited?: boolean;
  account_id?: number;
}

interface ImportPreview {
  records: Array<BillImport | IncomeImport>;
  validation_errors: ImportError[];
  total_records: number;
}

interface ImportResponse {
  success: boolean;
  processed: number;
  succeeded: number;
  failed: number;
  errors?: ImportError[];
}

interface FileImportModalProps {
  open: boolean;
  onClose: () => void;
  onImport: (file: File) => Promise<ImportResponse>;
  onPreview: (file: File) => Promise<ImportPreview>;
  title: string;
  acceptedFormats: string;
}

const FileImportModal: React.FC<FileImportModalProps> = ({
  open,
  onClose,
  onImport,
  onPreview,
  title,
  acceptedFormats,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [importResult, setImportResult] = useState<ImportResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setError(null);
    setImportResult(null);
    setLoading(true);

    try {
      const previewResult = await onPreview(selectedFile);
      setPreview(previewResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to preview file');
      setPreview(null);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const result = await onImport(file);
      setImportResult(result);
      if (result.success) {
        setTimeout(() => {
          onClose();
        }, 2000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
      try {
        setLoading(true);
        const previewResult = await onPreview(droppedFile);
        setPreview(previewResult);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to preview file');
        setPreview(null);
      } finally {
        setLoading(false);
      }
    }
  };

  const renderPreview = () => {
    if (!preview) return null;

    return (
      <Box sx={{ mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Preview
        </Typography>
        {preview.validation_errors.length > 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <AlertTitle>Validation Errors</AlertTitle>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Row</TableCell>
                    <TableCell>Field</TableCell>
                    <TableCell>Error</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {preview.validation_errors.map((error, index) => (
                    <TableRow key={index}>
                      <TableCell>{error.row}</TableCell>
                      <TableCell>{error.field}</TableCell>
                      <TableCell>{error.message}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Alert>
        )}
        <Typography>
          Total Records: {preview.total_records}
          {preview.validation_errors.length > 0 &&
            ` (${preview.validation_errors.length} errors)`}
        </Typography>
      </Box>
    );
  };

  const renderImportResult = () => {
    if (!importResult) return null;

    return (
      <Alert
        severity={importResult.success ? 'success' : 'error'}
        sx={{ mt: 2 }}
      >
        <AlertTitle>
          {importResult.success ? 'Import Successful' : 'Import Failed'}
        </AlertTitle>
        <Typography>
          Processed: {importResult.processed} records
          <br />
          Succeeded: {importResult.succeeded} records
          <br />
          Failed: {importResult.failed} records
        </Typography>
        {importResult.errors && importResult.errors.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="subtitle2">Errors:</Typography>
            <TableContainer component={Paper}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Row</TableCell>
                    <TableCell>Field</TableCell>
                    <TableCell>Error</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {importResult.errors.map((error, index) => (
                    <TableRow key={index}>
                      <TableCell>{error.row}</TableCell>
                      <TableCell>{error.field}</TableCell>
                      <TableCell>{error.message}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Alert>
    );
  };

  return (
    <Modal open={open} onClose={onClose}>
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '80%',
          maxWidth: 800,
          bgcolor: 'background.paper',
          boxShadow: 24,
          p: 4,
          maxHeight: '90vh',
          overflow: 'auto',
        }}
      >
        <Typography variant="h5" component="h2" gutterBottom>
          {title}
        </Typography>

        <Box
          sx={{
            border: '2px dashed #ccc',
            borderRadius: 2,
            p: 3,
            textAlign: 'center',
            mb: 2,
            cursor: 'pointer',
          }}
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            hidden
            ref={fileInputRef}
            accept={acceptedFormats}
            onChange={handleFileChange}
          />
          <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
          <Typography>
            Drag and drop a file here, or click to select a file
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Accepted formats: {acceptedFormats}
          </Typography>
        </Box>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ my: 2 }}>
            {error}
          </Alert>
        )}

        {renderPreview()}
        {renderImportResult()}

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleImport}
            disabled={
              !file ||
              loading ||
              (preview?.validation_errors.length ?? 0) > 0 ||
              importResult?.success
            }
          >
            {loading ? (
              <CircularProgress size={24} sx={{ mr: 1 }} />
            ) : (
              'Import Data'
            )}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
};

export default FileImportModal;
