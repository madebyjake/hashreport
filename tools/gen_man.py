#!/usr/bin/env python3
"""Generate man pages from program metadata and documentation."""

import sys
from datetime import datetime
from pathlib import Path

import click

sys.path.append(str(Path(__file__).parent.parent.parent))

from hashreport.cli import cli  # noqa: E402
from hashreport.config import get_config  # noqa: E402

MAN_PAGE_TEMPLATE = """\
.\\\" Man page for hashreport
.\\\" Contact hashreport@fastmail.com for corrections or typos.
.TH "HASHREPORT" "1" "{date}" "hashreport-{version}" "User Commands"
.ie \n(.g .ds Aq \\(aq
.el       .ds Aq '
.nh
.ad l

.SH "NAME"
\\fBhashreport\\fR \\- {summary}

.SH "SYNOPSIS"
.HP \\w'\\fBhashreport\\fR\\ 'u
\\fBhashreport\\fR \\fICOMMAND\\fR [\\fIOPTIONS\\fR...]

.SH "DESCRIPTION"
.PP
{description}

.SH "COMMANDS"
.PP
The following commands are available:
{commands}

.SH "OPTIONS"
.PP
These options apply to all commands:
{global_options}

.SH "EXIT STATUS"
.PP
\\fBhashreport\\fR exits 0 on success, 1 on error.

.SH "ENVIRONMENT"
.TP
\\fBPYTHONPATH\\fR
Modify Python import path.

.SH "FILES"
.TP
\\fI~/.config/hashreport/settings.toml\\fR
User configuration file.

.SH "EXAMPLES"
.PP
Generate MD5 hashes for all files in current directory:
.PP
.RS 4
\\fBhashreport scan .\\fR
.RE
.PP
Use SHA256 and output as JSON:
.PP
.RS 4
\\fBhashreport scan \\-a sha256 \\-f json /path/to/scan\\fR
.RE

.SH "BUGS"
.PP
Report bugs at: <{bug_url}>

.SH "AUTHOR"
.PP
{author}

.SH "COPYRIGHT"
.PP
Copyright \\(co {year} {author}\\&.
License AGPLv3+: GNU AGPL version 3 or later <https://gnu.org/licenses/agpl.html>\\&.
.br
This is free software: you are free to change and redistribute it\\&.
There is NO WARRANTY, to the extent permitted by law\\&.

.SH "SEE ALSO"
.PP
\\fBmd5sum\\fR(1), \\fBsha256sum\\fR(1)
.PP
Full documentation at: <{docs_url}>
"""


def format_command(cmd: click.Command, ctx: click.Context, parent: str = "") -> str:
    """Format a command for man page."""
    cmd_path = f"{parent} {cmd.name}".strip()
    result = [f".TP\n\\fB{cmd_path}\\fR"]
    if cmd.help:
        # Properly format command help text
        help_text = cmd.help.replace("\n", "\n.br\n")
        result.append(help_text)

    if isinstance(cmd, click.Group):
        result.append(".RS 4")  # Indent subcommands
        for subcmd_name in sorted(cmd.list_commands(ctx)):
            subcmd = cmd.get_command(ctx, subcmd_name)
            if subcmd:
                result.append(format_command(subcmd, ctx, cmd_path))
        result.append(".RE")  # End indentation

    params = cmd.get_params(ctx)
    if params:
        result.append('.RS 4\n.B "Options:"')
        for param in params:
            if isinstance(param, click.Option):
                opts = "/".join(f"\\fB{opt}\\fR" for opt in param.opts)
                if param.metavar:
                    opts += f" \\fI{param.metavar}\\fR"
                help_text = param.help.replace("\n", "\n.br\n") if param.help else ""
                result.append(f".TP\n{opts}\n{help_text}")
        result.append(".RE")

    return "\n".join(result)


def format_commands(ctx: click.Context) -> str:
    """Format all commands for man page."""
    result = []
    for cmd_name in sorted(ctx.command.list_commands(ctx)):
        cmd = ctx.command.get_command(ctx, cmd_name)
        if cmd:
            result.append(format_command(cmd, ctx))
    return "\n.PP\n".join(result)


def format_global_options(ctx: click.Context) -> str:
    """Format global options for man page."""
    result = []
    for param in ctx.command.get_params(ctx):
        if isinstance(param, click.Option):
            opts = "/".join(f"\\fB{opt}\\fR" for opt in param.opts)
            if param.metavar:
                opts += f" \\fI{param.metavar}\\fR"
            result.append(f".TP\n{opts}\n{param.help}")
    return "\n".join(result)


def generate_man_page() -> None:
    """Generate man page from CLI commands and metadata."""
    config = get_config()
    metadata = config.get_metadata()

    # Create context to inspect CLI structure
    ctx = click.Context(cli, info_name="hashreport")

    # Format content
    content = MAN_PAGE_TEMPLATE.format(
        date=datetime.now().strftime("%B %Y"),
        version=metadata["version"],
        summary="generate detailed file hash reports",
        description=metadata["description"].replace("\n", "\n.br\n"),
        commands=format_commands(ctx),
        global_options=format_global_options(ctx),
        author=metadata["authors"][0].split("<")[0].strip(),
        year=datetime.now().year,
        bug_url=metadata["urls"].get(
            "Issues", "https://github.com/madebyjake/hashreport/issues"
        ),
        docs_url=metadata["urls"].get(
            "Documentation", "https://github.com/madebyjake/hashreport"
        ),
    )

    # Ensure man directory exists
    man_dir = Path("man/man1")
    man_dir.mkdir(parents=True, exist_ok=True)

    # Write man page with proper permissions
    man_file = man_dir / "hashreport.1"
    man_file.write_text(content)
    man_file.chmod(0o644)  # Standard permission for man pages

    print(f"Generated man page: {man_file}")


if __name__ == "__main__":
    generate_man_page()
