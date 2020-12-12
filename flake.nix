{
  description = "Python script to generate various UT auxiliary mappings.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-20.09";
    flake-utils.url = "github:numtide/flake-utils";
    pyUTM.url = "github:umd-lhcb/pyUTM";
  };

  outputs = { self, nixpkgs, flake-utils, pyUTM }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ pyUTM.overlay ];
        };
      in
      rec {
        packages = {
          UT_Aux_mapping_Env = pkgs.python3.withPackages (ps: with ps; [
            # NOTE: plain 'pyUTM' won't work here as it is interpreted as
            #       an argument, instead of a package.
            pkgs.pythonPackages.pyUTM

            # Dev tools
            jedi
            flake8
            pylint
          ]);
        };

        defaultPackage = packages.UT_Aux_mapping_Env;
        devShell = packages.UT_Aux_mapping_Env.env;
      });
}
