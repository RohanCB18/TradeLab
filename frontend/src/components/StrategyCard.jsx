import { Link } from "react-router-dom";

function StrategyCard({ title, image, to }) {
  return (
    <Link to={to}>
      <div className="cursor-pointer rounded-lg overflow-hidden shadow hover:shadow-lg transition">
        <img src={image} alt={title} />
        <h3 className="p-4 font-semibold">{title}</h3>
      </div>
    </Link>
  );
}

export default StrategyCard;
