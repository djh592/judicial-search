import React, { useState } from 'react';
import Paper from '@mui/material/Paper';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import AdvancedSearchFields from './AdvancedSearchFields';
import { fetchSuggest } from '../api';

interface Props {
    onSearch: (userQuery: any) => void;
}

const SearchBox: React.FC<Props> = ({ onSearch }) => {
    const [query, setQuery] = useState('');
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [advanced, setAdvanced] = useState(false);
    const [fields, setFields] = useState({
        qw: '',
        ajmc: '',
        ay: '',
        fymc: '',
        spry: '',
        dsr: '',
    });

    const handleFieldChange = (field: string, value: string) => {
        setFields(prev => ({ ...prev, [field]: value }));
    };

    const handleInputChange = async (_: any, value: string) => {
        setQuery(value);
        if (value.trim()) {
            setLoading(true);
            try {
                const result = await fetchSuggest('ajName', value);
                setSuggestions(result);
            } finally {
                setLoading(false);
            }
        } else {
            setSuggestions([]);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSearch({ query, ...fields });
    };

    return (
        <Paper elevation={3} sx={{ p: 4, minWidth: 400, maxWidth: 600 }}>
            <form onSubmit={handleSubmit}>
                <Autocomplete
                    freeSolo
                    options={suggestions}
                    inputValue={query}
                    onInputChange={handleInputChange}
                    loading={loading}
                    filterOptions={x => x}
                    renderInput={(params) => (
                        <TextField
                            {...params}
                            label="请输入检索内容"
                            fullWidth
                            sx={{ mb: 2 }}
                        />
                    )}
                />
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ flex: 1 }}>
                        高级搜索
                    </Typography>
                    <IconButton onClick={() => setAdvanced(a => !a)} size="small">
                        {advanced ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                </Box>
                <Collapse in={advanced}>
                    <AdvancedSearchFields values={fields} onChange={handleFieldChange} />
                </Collapse>
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    fullWidth
                    sx={{ mt: 3 }}
                >
                    搜索
                </Button>
            </form>
        </Paper>
    );
};

export default SearchBox;