import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';

interface Props {
    result: any;
    onClick?: () => void;
}

const SearchResultItem: React.FC<Props> = ({ result, onClick }) => (
    <Card
        variant="outlined"
        sx={{ mb: 2, cursor: onClick ? 'pointer' : 'default', '&:hover': { boxShadow: 3 } }}
        onClick={onClick}
    >
        <CardContent>
            <Typography variant="h6" gutterBottom>
                {result.ajName || result.ajid}
            </Typography>
            {Array.isArray(result.labels) && result.labels.length > 0 && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
                    {result.labels.map((label: string) => (
                        <Chip key={label} label={label} size="small" color="success" />
                    ))}
                </Box>
            )}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 1 }}>
                {result.fymc && (
                    <Chip label={`法院：${Array.isArray(result.fymc) ? result.fymc.join('、') : result.fymc}`} size="small" color="primary" onClick={(e) => e.stopPropagation()} />
                )}
                {Array.isArray(result.spry) && result.spry.length > 0 && (
                    <Chip label={`审判人员：${result.spry.join('、')}`} size="small" color="secondary" onClick={(e) => e.stopPropagation()} />
                )}
                {Array.isArray(result.dsr) && result.dsr.length > 0 && (
                    <Chip label={`当事人：${result.dsr.join('、')}`} size="small" onClick={(e) => e.stopPropagation()} />
                )}
            </Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
                {(result.ajjbqk || '').slice(0, 100) || '无案件基本情况'}...
            </Typography>
            <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                    文书ID: {result.writId} | 得分: {result.score ?? '-'}
                </Typography>
            </Box>
        </CardContent>
    </Card>
);

export default SearchResultItem;