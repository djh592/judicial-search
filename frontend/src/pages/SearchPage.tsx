import { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import SearchResultList from '../components/SearchResultList';
import PaginationBar from '../components/PaginationBar';
import { fetchQueryResults } from '../api';
import NavBar from '../components/NavBar';

const PAGE_SIZE = 10;
const MAX_PAGES = 100;

const SearchPage: React.FC = () => {
    const { queryId } = useParams<{ queryId: string }>();
    const [searchParams, setSearchParams] = useSearchParams();
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<any[]>([]);
    const [totalPages, setTotalPages] = useState(1);
    const navigate = useNavigate();

    // 直接从 searchParams 读取 page，并限制在 1 ~ MAX_PAGES
    const pageParam = Number(searchParams.get('page')) || 1;
    const page = Math.max(1, Math.min(pageParam, MAX_PAGES));

    // 自动修正超出范围的页码
    useEffect(() => {
        if (pageParam !== page) {
            setSearchParams({ page: page.toString() });
        }
        // eslint-disable-next-line
    }, [pageParam, page, setSearchParams]);

    const handleItemClick = (item: any) => {
        navigate(`/detail/${item.ajId}`);
    };

    useEffect(() => {
        if (!queryId) return;
        setLoading(true);
        fetchQueryResults(queryId, page, PAGE_SIZE)
            .then(res => {
                setResults(res.results || []);
                setTotalPages(res.total_pages || 1);
            })
            .catch(() => {
                setResults([]);
                setTotalPages(1);
            })
            .finally(() => setLoading(false));
    }, [queryId, page]);

    const handlePageChange = (_: any, value: number) => {
        setSearchParams({ page: value.toString() });
    };

    return (
        <>
            <NavBar />
            <Box sx={{ maxWidth: 800, mx: 'auto', py: 4 }}>

                <Typography variant="h5" gutterBottom>
                    检索结果
                </Typography>
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', my: 6 }}>
                        <CircularProgress />
                    </Box>
                ) : results.length === 0 ? (
                    <Typography color="text.secondary" sx={{ mt: 4 }}>
                        暂无结果
                    </Typography>
                ) : (
                    <>
                        <SearchResultList results={results} onItemClick={handleItemClick} />
                        <PaginationBar
                            page={page}
                            totalPages={Math.min(totalPages, MAX_PAGES)}
                            onChange={handlePageChange}
                        />
                    </>
                )}
            </Box>
        </>
    );
};

export default SearchPage;