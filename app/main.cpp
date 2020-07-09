#include <iostream>
#include <regex>
#include <string>
#include "httplib.h"

int main(int argc, char* argv[])
{
	const std::string serverUrl(argv[1]);
	const std::string playerKey(argv[2]);

	std::cout << "ServerUrl: " << serverUrl << "; PlayerKey: " << playerKey << std::endl;
	
	const std::regex urlRegexp("http://(.+):(\\d+)");
	std::smatch urlMatches;
	if (!std::regex_search(serverUrl, urlMatches, urlRegexp) || urlMatches.size() != 3) {
		std::cerr << "Bad server url" << std::endl;
		return 1;
	}
	const std::string serverName = urlMatches[1];
	const int serverPort = std::stoi(urlMatches[2]);
	httplib::Client client(serverName, serverPort);
	const std::shared_ptr<httplib::Response> serverResponse = 
		client.Get((serverUrl + "?playerKey=" + playerKey).c_str());

	if (!serverResponse) {
		std::cerr << "No response from server" << std::endl;
		return 2;
	}
	
	if (serverResponse->status != 200) {
		std::cerr << "Server returned error: " <<
			httplib::detail::status_message(serverResponse->status) << 
			" (" << serverResponse->status << ")" << std::endl;
		return 3;
	}

	return 0;
}

