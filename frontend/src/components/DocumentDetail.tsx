import Paper from '@mui/material/Paper';
import DocumentHeader from './DocumentHeader';
import DocumentSection from './DocumentSection';

interface Props {
    detail: any;
}

const DocumentDetail: React.FC<Props> = ({ detail }) => (
    <Paper sx={{ p: 3 }}>
        <DocumentHeader
            ajName={detail.ajName}
            ajId={detail.ajId}
            writId={detail.writId}
            writName={detail.writName}
            labels={detail.labels}
            fymc={detail.fymc}
            spry={detail.spry}
            dsr={detail.dsr}
        />
        <DocumentSection title="案件基本情况" content={detail.ajjbqk} />
        <DocumentSection title="裁判分析过程" content={detail.cpfxgc} />
        <DocumentSection title="判决结果" content={detail.pjjg} />
        <DocumentSection title="正文" content={detail.qw} />
    </Paper>
);

export default DocumentDetail;