import Box from '@mui/material/Box';
import { useNavigate } from 'react-router-dom';
import TitleBar from '../components/TitleBar';
import SearchBox from '../components/SearchBox';
import { createQuery } from '../api';

const HomePage: React.FC = () => {
    const navigate = useNavigate();
    const handleSearch = async (userQuery: any) => {
        try {
            const resp = await createQuery({ user_query: userQuery });
            navigate(`/search/${resp.query_id}`);
        } catch {
            alert('创建查询失败，请重试');
        }
    };
    return (
        <Box sx={{
            minHeight: '100vh',
            background: 'linear-gradient(135deg, #e3f2fd 0%, #fff 100%)'
        }}>
            <TitleBar />
            <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '70vh'
            }}>
                <SearchBox onSearch={handleSearch} />
            </Box>
        </Box>
    );
};

export default HomePage;