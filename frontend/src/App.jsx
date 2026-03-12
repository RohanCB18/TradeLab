import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import StrategyDetail from './pages/StrategyDetail';
import Compare from './pages/Compare';
import './index.css';

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/strategy/:id" element={<StrategyDetail />} />
        <Route path="/compare" element={<Compare />} />
      </Routes>
    </>
  );
}
