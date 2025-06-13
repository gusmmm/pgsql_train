import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Route, Routes, Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  Grid,
  Button,
  Drawer,
  IconButton,
  Divider
} from '@mui/material';
import {
  Storage as StorageIcon,
  CloudCircle as CloudCircleIcon,
  Description as DescriptionIcon, // Schema icon
  Menu as MenuIcon,
  Home as HomeIcon,
  Dns as DnsIcon, // Database server icon
  FolderSpecial as FolderSpecialIcon, // Schema icon (alternative)
} from '@mui/icons-material';
import apiService from './services/apiService';
import TableSchemaViewer from './components/TableSchemaViewer';

function App() {
  const [dbStatus, setDbStatus] = useState(null);
  const [schemas, setSchemas] = useState([]);
  const [selectedSchema, setSelectedSchema] = useState(null);
  const [schemaDetails, setSchemaDetails] = useState(null);
  const [selectedTable, setSelectedTable] = useState(null);
  const [tableSchema, setTableSchema] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [loadingSchemas, setLoadingSchemas] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [loadingTableSchema, setLoadingTableSchema] = useState(false);
  const [error, setError] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchSchemas = useCallback(async () => {
    setLoadingSchemas(true);
    setError(null);
    try {
      const data = await apiService.getSchemas();
      setSchemas(data.schemas || []);
    } catch (err) {
      setError(`Failed to fetch schemas: ${err.message}`);
    } finally {
      setLoadingSchemas(false);
    }
  }, []);

  const fetchDbStatus = useCallback(async () => {
    setLoadingStatus(true);
    setError(null);
    try {
      const data = await apiService.getDbStatus();
      setDbStatus(data);
      if (data.status === 'online') {
        fetchSchemas();
      }
    } catch (err) {
      setError(`Failed to fetch DB status: ${err.message}`);
      setDbStatus({ status: 'offline', error: err.message });
    } finally {
      setLoadingStatus(false);
    }
  }, [fetchSchemas]);

  const fetchTableSchema = useCallback(async (schemaName, tableName) => {
    setSelectedTable(`${schemaName}.${tableName}`);
    setLoadingTableSchema(true);
    setError(null);
    setTableSchema(null);
    try {
      const data = await apiService.getTableSchema(schemaName, tableName);
      setTableSchema(data);
    } catch (err) {
      setError(`Failed to fetch schema for table ${schemaName}.${tableName}: ${err.message}`);
    } finally {
      setLoadingTableSchema(false);
    }
  }, []);

  useEffect(() => {
    fetchDbStatus();
  }, [fetchDbStatus]);

  const fetchSchemaDetails = async (schemaName) => {
    setSelectedSchema(schemaName);
    setLoadingDetails(true);
    setError(null);
    setSchemaDetails(null); // Clear previous details
    try {
      const data = await apiService.getSchemaDetails(schemaName);
      setSchemaDetails(data);
    } catch (err) {
      setError(`Failed to fetch schema details for ${schemaName}: ${err.message}`);
    } finally {
      setLoadingDetails(false);
    }
  };
  
  const toggleDrawer = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setDrawerOpen(open);
  };

  const drawerContent = (
    <Box
      sx={{ width: 250 }}
      role="presentation"
      onClick={toggleDrawer(false)}
      onKeyDown={toggleDrawer(false)}
    >
      <Toolbar />
      <Divider />
      <List>
        <ListItem button component={RouterLink} to="/">
          <ListItemIcon><HomeIcon /></ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItem>
        <ListItem button onClick={fetchDbStatus} disabled={loadingStatus}>
          <ListItemIcon><DnsIcon /></ListItemIcon>
          <ListItemText primary={loadingStatus ? "Checking Status..." : "Refresh DB Status"} />
        </ListItem>
      </List>
      <Divider />
      {dbStatus && dbStatus.status === 'online' && (
        <List>
          <ListItem>
            <Typography variant="h6" sx={{ ml: 1, mb:1 }}>Schemas</Typography>
          </ListItem>
          {loadingSchemas ? (
            <ListItem><CircularProgress size={24} /></ListItem>
          ) : schemas.length > 0 ? (
            schemas.map((schema) => (
              <ListItem 
                button 
                key={schema} 
                onClick={() => fetchSchemaDetails(schema)}
                selected={selectedSchema === schema}
              >
                <ListItemIcon><FolderSpecialIcon /></ListItemIcon>
                <ListItemText primary={schema} />
              </ListItem>
            ))
          ) : (
            <ListItem>
              <ListItemText primary="No schemas found or API error." />
            </ListItem>
          )}
        </List>
      )}
    </Box>
  );

  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={toggleDrawer(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              Paper DB Manager
            </Typography>
          </Toolbar>
        </AppBar>
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={toggleDrawer(false)}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
        >
          {drawerContent}
        </Drawer>
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - 250px)` },
          }}
        >
          <Toolbar /> {/* For spacing below AppBar */}
          <Container maxWidth="lg">
            <Routes>
              <Route path="/" element={<DashboardPage 
                                        dbStatus={dbStatus} 
                                        loadingStatus={loadingStatus} 
                                        error={error}
                                        selectedSchema={selectedSchema}
                                        schemaDetails={schemaDetails}
                                        loadingDetails={loadingDetails}
                                        selectedTable={selectedTable}
                                        tableSchema={tableSchema}
                                        loadingTableSchema={loadingTableSchema}
                                        onRefresh={fetchDbStatus}
                                        onTableSelect={fetchTableSchema}
                                      />} />
              {/* Add other routes here if needed */}
            </Routes>
          </Container>
        </Box>
      </Box>
    </Router>
  );
}

const DashboardPage = ({ 
  dbStatus, 
  loadingStatus, 
  error, 
  selectedSchema, 
  schemaDetails, 
  loadingDetails, 
  selectedTable,
  tableSchema,
  loadingTableSchema,
  onRefresh, 
  onTableSelect 
}) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
          <Typography variant="h5" gutterBottom component="div">
            Database Status
          </Typography>
          {loadingStatus ? (
            <CircularProgress />
          ) : dbStatus ? (
            <Alert severity={dbStatus.status === 'online' ? 'success' : 'error'}>
              Status: {dbStatus.status}
              {dbStatus.status === 'online' && dbStatus.host && (
                <>
                  <br />Host: {dbStatus.host}
                  <br />Port: {dbStatus.port}
                  <br />Database Name: {dbStatus.name}
                </>
              )}
              {dbStatus.error && <><br />Error: {dbStatus.error}</>}
            </Alert>
          ) : (
            <Alert severity="warning">Could not fetch database status.</Alert>
          )}
          <Button onClick={onRefresh} variant="outlined" sx={{mt: 2}} disabled={loadingStatus}>
            Refresh Status
          </Button>
        </Paper>
      </Grid>

      {error && (
        <Grid item xs={12}>
          <Alert severity="error">{error}</Alert>
        </Grid>
      )}

      {selectedSchema && (
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h5" gutterBottom component="div">
              Schema: {selectedSchema}
            </Typography>
            {loadingDetails ? (
              <CircularProgress />
            ) : schemaDetails ? (
              <Box>
                <Typography variant="h6">Tables:</Typography>
                {schemaDetails.tables && schemaDetails.tables.length > 0 ? (
                  <List dense>
                    {schemaDetails.tables.map((table) => (
                      <ListItem 
                        key={table} 
                        button 
                        onClick={() => onTableSelect(selectedSchema, table)}
                        selected={selectedTable === `${selectedSchema}.${table}`}
                      >
                        <ListItemIcon><StorageIcon fontSize="small" /></ListItemIcon>
                        <ListItemText 
                          primary={table} 
                          secondary={selectedTable === `${selectedSchema}.${table}` ? "Click to view schema" : "Click to view schema"}
                        />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2">No tables found.</Typography>
                )}

                <Typography variant="h6" sx={{ mt: 2 }}>Views:</Typography>
                {schemaDetails.views && schemaDetails.views.length > 0 ? (
                  <List dense>
                    {schemaDetails.views.map((view) => (
                      <ListItem key={view}>
                        <ListItemIcon><CloudCircleIcon fontSize="small" /></ListItemIcon>
                        <ListItemText primary={view} />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2">No views found.</Typography>
                )}

                <Typography variant="h6" sx={{ mt: 2 }}>Functions:</Typography>
                {schemaDetails.functions && schemaDetails.functions.length > 0 ? (
                  <List dense>
                    {schemaDetails.functions.map((func) => (
                      <ListItem key={func}>
                        <ListItemIcon><DescriptionIcon fontSize="small" /></ListItemIcon>
                        <ListItemText primary={func} />
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2">No functions found.</Typography>
                )}
              </Box>
            ) : (
              <Alert severity="info">No details available for this schema.</Alert>
            )}
          </Paper>
        </Grid>
      )}

      {selectedTable && (
        <Grid item xs={12}>
          <TableSchemaViewer 
            tableSchema={tableSchema}
            loading={loadingTableSchema}
            error={error}
          />
        </Grid>
      )}
    </Grid>
  );
};

export default App;
