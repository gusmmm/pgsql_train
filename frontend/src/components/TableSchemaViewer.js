import React from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Key as KeyIcon,
  Link as LinkIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const TableSchemaViewer = ({ tableSchema, loading, error }) => {
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={3}>
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>Loading table schema...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!tableSchema) {
    return (
      <Alert severity="info" sx={{ m: 2 }}>
        Select a table to view its schema
      </Alert>
    );
  }

  const getDataTypeDisplay = (column) => {
    let typeDisplay = column.data_type;
    
    if (column.max_length) {
      typeDisplay += `(${column.max_length})`;
    } else if (column.numeric_precision && column.numeric_scale !== null) {
      typeDisplay += `(${column.numeric_precision},${column.numeric_scale})`;
    } else if (column.numeric_precision) {
      typeDisplay += `(${column.numeric_precision})`;
    }
    
    return typeDisplay;
  };

  const isPrimaryKey = (columnName) => {
    return tableSchema.primaryKeys && tableSchema.primaryKeys.includes(columnName);
  };

  const getForeignKeyInfo = (columnName) => {
    return tableSchema.foreignKeys && tableSchema.foreignKeys.find(fk => fk.column === columnName);
  };

  return (
    <Paper sx={{ p: 2, m: 2 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Table Schema: {tableSchema.schemaName}.{tableSchema.tableName}
        </Typography>
        
        {tableSchema.rowCount !== null && (
          <Typography variant="body2" color="text.secondary">
            <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
            Rows: {tableSchema.rowCount?.toLocaleString() || 'Unknown'}
          </Typography>
        )}
      </Box>

      {/* Columns Table */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">
            Columns ({tableSchema.columns?.length || 0})
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Column Name</strong></TableCell>
                  <TableCell><strong>Data Type</strong></TableCell>
                  <TableCell><strong>Nullable</strong></TableCell>
                  <TableCell><strong>Default</strong></TableCell>
                  <TableCell><strong>Constraints</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tableSchema.columns?.map((column) => (
                  <TableRow key={column.name} hover>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {column.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {getDataTypeDisplay(column)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={column.is_nullable ? 'YES' : 'NO'} 
                        color={column.is_nullable ? 'default' : 'primary'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace" color="text.secondary">
                        {column.default_value || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {isPrimaryKey(column.name) && (
                          <Chip
                            icon={<KeyIcon />}
                            label="PRIMARY KEY"
                            color="warning"
                            size="small"
                          />
                        )}
                        {getForeignKeyInfo(column.name) && (
                          <Chip
                            icon={<LinkIcon />}
                            label={`FK → ${getForeignKeyInfo(column.name).references_table}`}
                            color="info"
                            size="small"
                          />
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* Primary Keys */}
      {tableSchema.primaryKeys && tableSchema.primaryKeys.length > 0 && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              Primary Keys ({tableSchema.primaryKeys.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {tableSchema.primaryKeys.map((pk) => (
                <Chip
                  key={pk}
                  icon={<KeyIcon />}
                  label={pk}
                  color="warning"
                  variant="outlined"
                />
              ))}
            </Box>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Foreign Keys */}
      {tableSchema.foreignKeys && tableSchema.foreignKeys.length > 0 && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">
              Foreign Keys ({tableSchema.foreignKeys.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Column</strong></TableCell>
                    <TableCell><strong>References</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tableSchema.foreignKeys.map((fk, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {fk.column}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {fk.references_schema}.{fk.references_table}.{fk.references_column}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>
      )}
    </Paper>
  );
};

export default TableSchemaViewer;
