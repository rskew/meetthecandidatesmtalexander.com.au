{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let pkgs = import nixpkgs { system = "x86_64-linux"; };
        python = pkgs.python3.withPackages (ps: with ps; [ chevron click ]);
    in {
      packages.x86_64-linux.default = pkgs.writeShellScriptBin "answers-to-html" ''
        mkdir -p site/candidates
        ${python}/bin/python ${./build-site.py} ${./responses.csv} ${./candidate.mustache.html} ./site/candidates ${./ward.mustache.html} ./site/wards
      '';
    };
}

