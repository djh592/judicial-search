import SearchResultItem from './SearchResultItem';

interface Props {
    results: any[];
    onItemClick?: (item: any) => void;
}

const SearchResultList: React.FC<Props> = ({ results, onItemClick }) => (
    <>
        {results.map((item, idx) => (
            <SearchResultItem
                key={item.ajid || item.writId || idx}
                result={item}
                onClick={onItemClick ? () => onItemClick(item) : undefined}
            />
        ))}
    </>
);

export default SearchResultList;