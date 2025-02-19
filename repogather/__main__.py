import asyncio
from .interfaces.cli.parser import create_parser
from .interfaces.cli.commands import handle_gather, handle_analyze

def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == 'analyze':
        asyncio.run(handle_analyze(args))
    else:
        asyncio.run(handle_gather(args))

if __name__ == '__main__':
    main() 