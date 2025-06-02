import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import DetailPage from './pages/DetailPage';

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/search/:queryId" element={<SearchPage />} />
      <Route path="/detail/:docId" element={<DetailPage />} />
    </Routes>
  </BrowserRouter>
);

export default App;