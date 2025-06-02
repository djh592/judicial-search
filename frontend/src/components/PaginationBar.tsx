import Pagination from '@mui/material/Pagination';
import Stack from '@mui/material/Stack';

interface Props {
    page: number;
    totalPages: number;
    onChange: (event: React.ChangeEvent<unknown>, value: number) => void;
}

const PaginationBar: React.FC<Props> = ({ page, totalPages, onChange }) => (
    <Stack spacing={2} alignItems="center" sx={{ my: 3 }}>
        <Pagination
            count={totalPages} // 这里必须是受控的最大页数
            page={page}
            onChange={onChange}
            color="primary"
            shape="rounded"
            showFirstButton
            showLastButton
        />
    </Stack>
);

export default PaginationBar;