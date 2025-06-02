import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import { fetchDocumentDetail } from '../api';
import DocumentDetail from '../components/DocumentDetail';

const DetailPage: React.FC = () => {
    const { docId } = useParams<{ docId: string }>();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [detail, setDetail] = useState<any>(null);

    useEffect(() => {
        if (!docId) return;
        setLoading(true);
        setError(null);
        fetchDocumentDetail(docId)
            .then(setDetail)
            .catch(() => setError('未找到该文书详情'))
            .finally(() => setLoading(false));
    }, [docId]);

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error || !detail) {
        return (
            <Typography color="error" sx={{ mt: 8, textAlign: 'center' }}>
                {error || '未找到该文书详情'}
            </Typography>
        );
    }

    return (
        <Box sx={{ maxWidth: 900, mx: 'auto', py: 4 }}>
            <DocumentDetail detail={detail} />
        </Box>
    );
};

export default DetailPage;