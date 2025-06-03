import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { useNavigate, useLocation } from 'react-router-dom';

const NavBar: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <AppBar position="static" color="default" elevation={1}>
            <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => navigate('/')}>
                    司法搜索引擎
                </Typography>
                {location.pathname.startsWith('/search') && (
                    <Button color="inherit" onClick={() => navigate('/')}>返回首页</Button>
                )}
                {location.pathname.startsWith('/detail') && (
                    <Button color="inherit" onClick={() => navigate(-1)}>返回搜索</Button>
                )}
            </Toolbar>
        </AppBar>
    );
};

export default NavBar;