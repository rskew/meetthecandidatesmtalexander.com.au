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
        ${python}/bin/python ${./render_templates.py} ${./data.toml} ${./responses.csv} ${./index.template.html} ${./media.template.html} ./site ${./candidate.template.html} ./site/candidates ${./ward.template.html} ./site/wards
      '';
      packages.x86_64-linux.watch = pkgs.writeShellScriptBin "watch-rebuild" ''
        RENDER_CMD="${python}/bin/python render_templates.py data.toml responses.csv index.template.html media.template.html site/ candidate.template.html site/candidates ward.template.html site/wards"
        bash -c "$RENDER_CMD"
        while ${pkgs.inotify-tools}/bin/inotifywait -e modify .; do bash -c "$RENDER_CMD"; done
      '';
      packages.x86_64-linux.process-images = pkgs.writeShellScriptBin "process-images" ''
        set -eux
        mkdir -p site/images
        ${pkgs.imagemagick}/bin/magick images/439336115_852369146929945_141540076818859956_n.jpg -crop 1365x1365+0+0 -strip -interlace Plane site/images/rosie_annear.jpg
        ${pkgs.imagemagick}/bin/magick images/451655473_122113545692372569_6059698426683280347_n.jpg -crop 1494x1494+0+0 -strip -interlace Plane site/images/lucas_maddock.jpg
        ${pkgs.imagemagick}/bin/magick images/Councillor_T_Cordy.jpg -crop 187x187+0+0 -strip -interlace Plane site/images/tony_cordy.jpg
        ${pkgs.imagemagick}/bin/magick images/Gavan\ Thomson\ jmp_240601_3522\ RT\ .jpg -crop 7729x7729+2000+0 -resize 1500x1500 -strip -interlace Plane site/images/gavan_thomson.jpg
        ${pkgs.imagemagick}/bin/magick images/Kerrie\ Allen_JPG_002.jpg -crop 762x762+0+0 -strip -interlace Plane site/images/kerrie_allen.jpg
        ${pkgs.imagemagick}/bin/magick images/mattd.jpg -crop 452x452+0+0 -strip -interlace Plane site/images/matt_driscoll.jpg
        ${pkgs.imagemagick}/bin/magick images/rosalie.jpg -crop 480x480+100+0 -strip -interlace Plane site/images/rosalie_hastwell.jpg
        ${pkgs.imagemagick}/bin/magick images/Screen\ Shot\ 2024-09-30\ at\ 7.06.08\ PM.png -crop 585x760+2+0 -gravity center -background "#d7d6ca" -extent 760x760 -strip -interlace Plane site/images/toby_heydon.png
        ${pkgs.imagemagick}/bin/magick images/Screenshot\ 2024-09-27\ 192503.png -crop 688x688+42+0 -strip -interlace Plane site/images/ken_price.png
        ${pkgs.imagemagick}/bin/magick images/_\ Walker,\ Phillip_3.jpeg -crop 1780x1780+0+0 -resize 1500x1500 -strip -interlace Plane site/images/phillip_walker.jpg
        ${pkgs.imagemagick}/bin/magick images/458597953_3668763250051571_1277882094949920310_n.jpg -crop 2730x2730+800+0 -resize 1500x1500 -strip -interlace Plane site/images/kelly_ann_blake.jpg
        cp images/maltby_150x150.jpg site/images/bill_maltby.jpg
        ${pkgs.imagemagick}/bin/magick images/max01.jpg -resize 1000x1000 -strip -interlace Plane site/images/max_lesser.jpg
      '';
    };
}

