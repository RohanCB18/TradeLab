import { useParams } from "react-router-dom";
import { strategies } from "../strategies";

// Learn components
import StrategyHero from "../components/learn/StrategyHero";
import StrategyOverview from "../components/learn/StrategyOverview";
import StrategyVisual from "../components/learn/StrategyVisual";
import StrategyRules from "../components/learn/StrategyRules";
import StrategyConditions from "../components/learn/StrategyConditions";
import StrategyParameters from "../components/learn/StrategyParameters";
import StrategyRisks from "../components/learn/StrategyRisks";
import StrategyCTA from "../components/learn/StrategyCTA";

function StrategyDetail() {
  const { strategyId } = useParams();

  const strategy = strategies[strategyId];

  // Guard: invalid route
  if (!strategy) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-24 text-center">
        <h1 className="text-3xl font-bold mb-4">
          Strategy Not Found
        </h1>
        <p className="text-gray-600">
          The requested trading strategy does not exist.
        </p>
      </div>
    );
  }

  const { content, visuals, config } = strategy;

  return (
    <div className="max-w-6xl mx-auto px-6 py-20 space-y-20">
      {/* 1. Hero */}
      <StrategyHero hero={content.hero} />

      {/* 2. Overview */}
      <StrategyOverview overview={content.overview} />

      {/* 3. Teaching Visuals */}
      <StrategyVisual visuals={visuals} />

      {/* 4. Trading Rules */}
      <StrategyRules rules={content.rules} />

      {/* 5. Market Conditions */}
      <StrategyConditions conditions={content.conditions} />

      {/* 6. Parameters */}
      <StrategyParameters parameters={content.parameters} />

      {/* 7. Risks */}
      <StrategyRisks risks={content.risks} />

      {/* 8. CTA */}
      <StrategyCTA config={config} />
    </div>
  );
}

export default StrategyDetail;
