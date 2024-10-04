{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let pkgs = import nixpkgs { system = "x86_64-linux"; };
        python = pkgs.python3.withPackages (ps: with ps; [ chevron click ]);
    in rec {
      packages.x86_64-linux.default = pkgs.writeShellScriptBin "answers-to-html" ''
        mkdir -p site/candidates
        ${python}/bin/python ${./build-site.py} ${./data.toml} ${./responses.csv} ${./index.template.html} ./site ${./candidate.template.html} ./site/candidates ${./ward.template.html} ./site/wards
      '';
      packages.x86_64-linux.watch = pkgs.writeShellScriptBin "watch-rebuild" ''
        while ${pkgs.inotify-tools}/bin/inotifywait -e modify .; do ${python}/bin/python build-site.py data.toml responses.csv index.template.html site/ candidate.template.html site/candidates ward.template.html site/wards; done
      '';
    };
}

