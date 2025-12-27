import { meanReversionStrategy } from "./meanReversion";
import { scalpingStrategy } from "./scalping";
import { momentumStrategy } from "./momentum";

export const strategies = {
  "mean-reversion": meanReversionStrategy,
  scalping: scalpingStrategy,
  momentum: momentumStrategy,
};
