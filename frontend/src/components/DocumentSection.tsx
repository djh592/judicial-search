import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

interface Props {
    title: string;
    content?: string;
}

const DocumentSection: React.FC<Props> = ({ title, content }) => {
    if (!content) return null;
    return (
        <Box sx={{ mb: 3 }}>
            <Typography variant="h6" color="primary" gutterBottom>
                {title}
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                {content}
            </Typography>
        </Box>
    );
};

export default DocumentSection;