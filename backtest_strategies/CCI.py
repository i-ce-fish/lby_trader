from pandas import DataFrame
from talib._ta_lib import CCI
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from backtest_strategies.backtest_strategy_template import BacktestStrategyTemplate


class CCIStrategy(BacktestStrategyTemplate):

    def get_singal(self, df: DataFrame):
        cci = self.get_scores(df)
        last_cci = cci[-1]
        previous_cci = cci[-2]

        # 上穿-100
        if last_cci > -100 > previous_cci or last_cci > 100 > previous_cci:
            return 1

        # 下穿-100
        if last_cci < 100 < previous_cci  or last_cci < -100 < previous_cci:
            return 0

        return -1

    def get_scores(self, df: DataFrame):
        return CCI(df.high, df.low, df.close, timeperiod=14)
