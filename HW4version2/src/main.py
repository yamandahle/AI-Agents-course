from hw4.sdk.sdk import HW4SDK


def main() -> None:
    sdk = HW4SDK()
    print(f"HW4 SDK initialized — version {sdk.config.get('version')}")


if __name__ == "__main__":
    main()
