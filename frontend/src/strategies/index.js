import { meanReversionStrategy } from "./meanReversion";
import { scalpingStrategy } from "./scalping";

export const strategies = {
  "mean-reversion": meanReversionStrategy,
  scalping: scalpingStrategy,
};
