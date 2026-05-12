from utils import get_logger

log = get_logger("port_scanner")

def parse_port(ports: str) -> set:
    result = set()

    for part in ports.split(","):
        part = part.strip()
        try:
            if '-' in part:
                start, end = part.split("-", 1)
                start = int(start)
                end = int(end)

                if start > end:
                    start, end = end, start
                result.update(range(start, end + 1))
            else:
                result.add(int(part))

        except ValueError:
            log.error(f"Invalid port format: ({part})")

    result = {
        p for p in result
        if 1 <= p <= 65535
    }

    if len(result) > 2000:
        log.warning(f"Large port scan detected ({len(result)}) ports")

    return result