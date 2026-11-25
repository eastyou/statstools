"""支持 ``python -m statstools`` 运行。"""

import sys

from statstools.cli import main

if __name__ == "__main__":
    sys.exit(main())
