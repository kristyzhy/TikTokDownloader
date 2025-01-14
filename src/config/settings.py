from json import dump
from json import load
from json.decoder import JSONDecodeError
from platform import system
from types import SimpleNamespace
from typing import TYPE_CHECKING

from ..custom import ERROR
from ..translation import _

if TYPE_CHECKING:
    from ..tools import ColorfulConsole
    from pathlib import Path

__all__ = ["Settings"]


class Settings:
    encode = "UTF-8-SIG" if system() == "Windows" else "UTF-8"
    default = {
        "accounts_urls": [
            {
                "mark": "",
                "url": "",
                "tab": "",
                "earliest": "",
                "latest": "",
                "enable": True,
            },
        ],
        "accounts_urls_tiktok": [
            {
                "mark": "",
                "url": "",
                "tab": "",
                "earliest": "",
                "latest": "",
                "enable": True,
            },
        ],
        "mix_urls": [
            {
                "mark": "",
                "url": "",
                "enable": True,
            },
        ],
        "mix_urls_tiktok": [
            {
                "mark": "",
                "url": "",
                "enable": True,
            },
        ],
        "owner_url": {
            "mark": "",
            "url": "",
            "uid": "",
            "sec_uid": "",
            "nickname": "",
        },
        "owner_url_tiktok": None,
        "root": "",
        "folder_name": "Download",
        "name_format": "create_time type nickname desc",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "split": "-",
        "folder_mode": False,
        "music": False,
        "truncate": 50,
        "storage_format": "",
        "cookie": "",
        "cookie_tiktok": "",
        "dynamic_cover": False,
        "original_cover": False,
        "proxy": None,
        "proxy_tiktok": None,
        "twc_tiktok": "",
        "download": True,
        "max_size": 0,
        "chunk": 1024 * 1024 * 2,  # 每次从服务器接收的数据块大小
        "timeout": 10,
        "max_retry": 5,  # 重试最大次数
        "max_pages": 0,
        "run_command": "",
        "ffmpeg": "",
        "douyin_platform": True,
        "tiktok_platform": True,
        "browser_info": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36",
            "pc_libra_divert": "Windows",
            "browser_platform": "Win32",
            "browser_name": "Chrome",
            "browser_version": "126.0.0.0",
            "engine_name": "Blink",
            "engine_version": "126.0.0.0",
            "os_name": "Windows",
            "os_version": "10",
            "webid": "",
        },
        "browser_info_tiktok": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/131.0.0.0 Safari/537.36",
            "app_language": "zh-Hans",
            "browser_language": "zh-SG",
            "browser_name": "Mozilla",
            "browser_platform": "Win32",
            "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/131.0.0.0 Safari/537.36",
            "language": "zh-Hans",
            "os": "windows",
            "priority_region": "CN",
            "region": "US",
            "tz_name": "Asia/Shanghai",
            "webcast_language": "zh-Hans",
            "device_id": "",
        }
    }  # 默认配置

    def __init__(self, root: "Path", console: "ColorfulConsole"):
        self.file = root.joinpath("./settings.json")  # 配置文件
        self.console = console

    def __create(self) -> dict:
        """创建默认配置文件"""
        with self.file.open("w", encoding=self.encode) as f:
            dump(self.default, f, indent=4, ensure_ascii=False)
        self.console.info(
            _("创建默认配置文件 settings.json 成功！\n"
              "请参考项目文档的快速入门部分，设置 Cookie 后重新运行程序！\n"
              "建议根据实际使用需求修改配置文件 settings.json！\n"),
        )
        return self.default

    def read(self) -> dict:
        """读取配置文件，如果没有配置文件，则生成配置文件"""
        try:
            if self.file.exists():
                with self.file.open("r", encoding=self.encode) as f:
                    return self.__check(load(f))
            return self.__create()  # 生成的默认配置文件必须设置 cookie 才可以正常运行
        except JSONDecodeError:
            self.console.error(
                _("配置文件 settings.json 格式错误，请检查 JSON 格式！"),
            )
            return self.default  # 读取配置文件发生错误时返回空配置

    def __check(self, data: dict) -> dict:
        default_keys = self.default.keys()
        data = self.__compatible_with_old_settings(data)
        data_keys = set(data.keys())
        if not (miss := default_keys - data_keys):
            return data
        if self.console.input(
                _("配置文件 settings.json 缺少 {missing_params} 参数，是否需要生成默认配置文件(YES/NO): ").format(
                    missing_params=', '.join(miss)
                ),
                style=ERROR,
        ).upper() == "YES":
            self.__create()
        self.console.warning(_("本次运行将会使用各项参数默认值，程序功能可能无法正常使用！"), )
        return self.default

    def update(self, settings: dict | SimpleNamespace):
        """更新配置文件"""
        with self.file.open("w", encoding=self.encode) as f:
            dump(
                settings if isinstance(
                    settings,
                    dict) else vars(settings),
                f,
                indent=4,
                ensure_ascii=False)
        self.console.info(_("保存配置成功！"), )

    def __compatible_with_old_settings(self, data: dict, ) -> dict:
        """兼容旧版本配置文件"""
        if "default_mode" in data:
            self.console.info("配置文件 default_mode 参数已变更为 run_command 参数，请注意修改配置文件！")
            data["run_command"] = data.get(
                "run_command",
                data.get(
                    "default_mode",
                    "",
                ),
            )  # TODO: 暂时兼容旧版本配置文件，未来将会移除
        if "update_cookie" in data:
            self.console.info("配置文件 update_cookie 参数已变更为 douyin_platform 参数，请注意修改配置文件！")
            data["douyin_platform"] = data.get(
                "douyin_platform",
                data.get(
                    "update_cookie",
                    True,
                ),
            )  # TODO: 暂时兼容旧版本配置文件，未来将会移除
        if "update_cookie_tiktok" in data:
            self.console.info("配置文件 update_cookie_tiktok 参数已变更为 tiktok_platform 参数，请注意修改配置文件！")
            data["tiktok_platform"] = data.get(
                "tiktok_platform",
                data.get(
                    "update_cookie_tiktok",
                    True,
                ),
            )  # TODO: 暂时兼容旧版本配置文件，未来将会移除
        return data
