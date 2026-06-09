# homebrew-formula.rb
# Para instalar: brew tap ricardogatica/bahia && brew install bahia

class Bahia < Formula
  desc "Monitor and manage open ports on macOS"
  homepage "https://github.com/ricardogatica/bahia"
  url "https://github.com/ricardogatica/bahia/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  license "Apache-2.0"

  depends_on "python@3.11"

  def install
    # Install Python package
    system "#{Formula["python@3.11"].opt_bin}/python3.11", "-m", "pip", "install",
           "--quiet", "--no-deps", "--prefix=#{prefix}", "."
  end

  def post_install
    # Ensure executable is in place
    bin.install "bahia"
  end

  test do
    system "#{bin}/bahia", "--help" rescue true
  end
end
