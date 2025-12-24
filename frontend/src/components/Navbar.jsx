import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="w-full border-b bg-white">
      <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div className="text-xl font-bold">TradeLab</div>

        <div className="flex gap-6">
          <Link to="/">Home</Link>
          <Link to="/learn">Learn</Link>
          <Link to="/test">Test</Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
