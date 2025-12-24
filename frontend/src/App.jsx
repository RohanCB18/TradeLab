import { Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import Learn from "./pages/Learn";
import StrategyDetail from "./pages/StrategyDetail";
import Test from "./pages/Test";

function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/learn/:strategyId" element={<StrategyDetail />} />
        <Route path="/test" element={<Test />} />
      </Route>
    </Routes>
  );
}

export default App;
