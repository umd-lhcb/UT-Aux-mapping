{
  description = "Python script to generate various UT auxiliary mappings.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-20.09";
    flake-utils.url = "github:numtide/flake-utils";
    pyUTM.url = "github:umd-lhcb/pyUTM";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, pyUTM, flake-compat }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ pyUTM.overlay ];
        };
      in
      rec {
        packages = rec {
          UT_Aux_mapping_Env = pkgs.python3.withPackages (ps: with ps; [
            # NOTE: plain 'pyUTM' won't work here as it is interpreted as
            #       an argument, instead of a package.
            pkgs.pythonPackages.pyUTM

            # Other dependencies
            tabulate

            # Dev tools
            jedi
            flake8
            pylint
          ]);
          UT_Aux_mapping_Dev = pkgs.mkShell {
            buildInputs = [
              UT_Aux_mapping_Env
              (pkgs.texlive.combine {
                inherit (pkgs.texlive)
                  scheme-basic
                  booktabs
                  amsmath
                  tcolorbox
                  makecell
                  # Implicit dependencies
                  environ
                  trimspaces
                  pgf
                  xcolor
                  etoolbox
                  ;
              })
            ];
          };
        };

        defaultPackage = packages.UT_Aux_mapping_Env;
        devShell = packages.UT_Aux_mapping_Dev;
      });
}
