import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const TitleBar: React.FC = () => (
  <Box sx={{ py: 4, textAlign: 'center' }}>
    <Typography variant="h3" fontWeight="bold" color="primary">
      法律文书智能检索系统
    </Typography>
  </Box>
);

export default TitleBar;