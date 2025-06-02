import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';
import Button from '@mui/material/Button';
import { useEffect, useState, ChangeEvent } from 'react';
import { fetchAllLabels } from '../api';
import * as mammoth from 'mammoth';

interface Props {
    values: Record<string, string>;
    onChange: (field: string, value: string) => void;
}

const AdvancedSearchFields: React.FC<Props> = ({ values, onChange }) => {
    const [labels, setLabels] = useState<string[]>([]);

    useEffect(() => {
        fetchAllLabels().then(setLabels);
    }, []);

    const handleFileChange = async (e: ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (file.type === 'text/plain') {
            // txt
            const reader = new FileReader();
            reader.onload = (event) => {
                const text = event.target?.result as string;
                onChange('qw', text);
            };
            reader.readAsText(file, 'utf-8');
        } else if (
            file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
            file.name.endsWith('.docx')
        ) {
            // docx
            const arrayBuffer = await file.arrayBuffer();
            const result = await mammoth.extractRawText({ arrayBuffer });
            onChange('qw', result.value);
        } else {
            alert('仅支持txt, docx文件');
        }
    };

    return (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 2 }}>
            <Box sx={{ flex: 1, minWidth: 200 }}>
                <TextField
                    label="全文检索"
                    value={values.qw}
                    onChange={e => onChange('qw', e.target.value)}
                    fullWidth
                    multiline
                    minRows={3}
                />
                <Button
                    variant="outlined"
                    component="label"
                    size="small"
                    sx={{ mt: 1 }}
                >
                    上传文件
                    <input
                        type="file"
                        accept=".txt,.docx,.pdf"
                        hidden
                        onChange={handleFileChange}
                    />
                </Button>
            </Box>
            <TextField label="案件名称" value={values.ajmc} onChange={e => onChange('ajmc', e.target.value)} fullWidth />
            <Autocomplete
                options={labels}
                value={values.ay || ''}
                onChange={(_, value) => onChange('ay', value || '')}
                renderInput={(params) => <TextField {...params} label="案由" fullWidth />}
                fullWidth
                sx={{ minWidth: 200 }}
            />
            <TextField label="法院名称" value={values.fymc} onChange={e => onChange('fymc', e.target.value)} fullWidth />
            <TextField label="审判人员" value={values.spry} onChange={e => onChange('spry', e.target.value)} fullWidth />
            <TextField label="当事人" value={values.dsr} onChange={e => onChange('dsr', e.target.value)} fullWidth />
        </Box>
    );
};

export default AdvancedSearchFields;