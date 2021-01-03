# coding:utf-8
import re
import time
from typing import Optional

from easytrader import exceptions
from easytrader.utils.perf import perf_clock
from easytrader.utils.win_gui import SetForegroundWindow, ShowWindow, win32defines


class PopDialogHandler:
    def __init__(self, app):
        self._app = app

    @staticmethod
    def _set_foreground(window):
        if window.has_style(win32defines.WS_MINIMIZE):  # if minimized
            ShowWindow(window.wrapper_object(), 9)  # restore window state
        else:
            SetForegroundWindow(window.wrapper_object())  # bring to front

    @perf_clock
    def handle(self, title):
        if any(s in title for s in {"提示信息", "委托确认", "网上交易用户协议", "撤单确认"}):
            self._submit_by_shortcut()
            return None

        if "提示" in title:
            content = self._extract_content()
            self._submit_by_click()
            return  {'state': 'fail','content':content}

        content = self._extract_content()
        self._close()
        return {"message": "unknown message: {}".format(content)}

    def _extract_content(self):
        return self._app.top_window().Static.window_text()

    @staticmethod
    def _extract_entrust_id(content):
        # return re.search(r"[\da-zA-Z]+", content).group()
        return re.findall(r"[\da-zA-Z]+", content)

    def _submit_by_click(self):
        try:
            self._app.top_window()["确定"].click()
        except Exception as ex:
            self._app.Window_(best_match="Dialog", top_level_only=True).ChildWindow(
                best_match="确定"
            ).click()

    def _submit_by_shortcut(self):
        self._set_foreground(self._app.top_window())
        self._app.top_window().type_keys("%Y", set_foreground=False)

    def _close(self):
        self._app.top_window().close()


class TradePopDialogHandler(PopDialogHandler):
    @perf_clock
    def handle(self, title) -> Optional[dict]:
        if title == "委托确认":#买入 1768  卖出 1041   单一 1040 Static7
            content = self._app.top_window().Static2.window_text()
            if len(content)>3:
                price = re.findall(r"价格：(\d+\.\d+)", content)[0]
                return {'price':float(price)}
            
            buyContent = self._app.top_window().Static3.window_text()
            sellContent = self._app.top_window().Static5.window_text()
            buyprice = re.findall(r"价格：(\d+\.\d+)", buyContent)[0]
            sellprice = re.findall(r"价格：(\d+\.\d+)", sellContent)[0]
            self._submit_by_shortcut()
            return {
                'buyprice':float(buyprice),
                'sellprice':float(sellprice)
                }

        if title == "提示信息":
            content = self._extract_content()
            if "超出涨跌停" in content:
                self._submit_by_shortcut()
                return None

            if "委托价格的小数价格应为" in content:
                self._submit_by_shortcut()
                return None

            if "逆回购" in content:
                self._submit_by_shortcut()
                return None

            if "正回购" in content:
                self._submit_by_shortcut()
                return None

            return None

        if title == "提示":
            content = self._extract_content()
            # content = '''您的卖出委托已成功提交，合同编号：14117。您的买入委托已成功提交，合同编号：14115。'''
            if "成功" in content:
                
                if len(content) > 23:

                    result = {'state': 'success'}
                    data = re.findall(r"\d{5}", content)
                    if len(data) == 2:
                        if content.find('卖出委托') > 20:
                            result['卖出合同'] = data[1]
                            result['买入合同'] = data[0]
                        else:
                            result['卖出合同'] = data[0]
                            result['买入合同'] = data[1]

                    else:
                        self._submit_by_click()
                        return {'state': 'fail','content':content,'错误合同':data[0]}

                else:
                    result = {'state': 'success'}
                    data = re.findall(r"\d{5}", content)
                    result['成交合同'] = data[0]
                
                self._submit_by_click()
                return result

            self._submit_by_click()
            time.sleep(0.05)
            return {'state': 'fail','content':content}
        return None
