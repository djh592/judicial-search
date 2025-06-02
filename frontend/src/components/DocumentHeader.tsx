import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';

interface Props {
    ajName?: string;
    ajId?: string;
    writId?: string;
    writName?: string;
    labels?: string[];
    fymc?: string | string[];
    spry?: string[];
    dsr?: string[];
}

const DocumentHeader: React.FC<Props> = ({ ajName, ajId, writId, writName, labels, fymc, spry, dsr }) => (
    <Box sx={{ mb: 2 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
            {ajName || '案件名称未知'}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
            案件ID: {ajId}　|　文书ID: {writId}　|　文书名称: {writName}
        </Typography>
        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {labels && labels.length > 0 && labels.map(label => (
                <Chip key={label} label={label} size="small" color="success" sx={{ mr: 1, mb: 1 }} onClick={e => e.stopPropagation()} />
            ))}
            {fymc && (
                <Chip
                    label={`法院：${Array.isArray(fymc) ? fymc.join('、') : fymc}`}
                    size="small"
                    color="primary"
                    sx={{ mr: 1, mb: 1 }}
                    onClick={e => e.stopPropagation()}
                />
            )}
            {spry && spry.length > 0 && (
                <Chip
                    label={`审判人员：${spry.join('、')}`}
                    size="small"
                    color="secondary"
                    sx={{ mr: 1, mb: 1 }}
                    onClick={e => e.stopPropagation()}
                />
            )}
            {dsr && dsr.length > 0 && (
                <Chip
                    label={`当事人：${dsr.join('、')}`}
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                    onClick={e => e.stopPropagation()}
                />
            )}
        </Box>
    </Box>
);

export default DocumentHeader;