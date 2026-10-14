import re, sys
from pathlib import Path
p=Path("pins.yaml"); s=p.read_text()
s2=re.sub(rf"(- slug: {re.escape(sys.argv[1])}\n(?:  .*\n|    .*\n)*?  status: )(approved|draft)", r"\1posted", s, count=1)
print("changed" if s2!=s else "UNCHANGED"); p.write_text(s2)
