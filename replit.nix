{ pkgs }: {
  deps = [
    pkgs.sqlite-interactive.bin
    pkgs.sqlite.bin
  ];
}