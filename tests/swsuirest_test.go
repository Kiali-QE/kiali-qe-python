package tests

import (
	"fmt"
	"github.com/sayems/golang.webdriver/selenium/pages"
	"github.com/stretchr/testify/assert"
	"github.com/tebeka/selenium"
	"gopkg.in/resty.v1"
	"os"
	"testing"
)

var driver selenium.WebDriver
var page pages.Page

func TestUIRest(t *testing.T) {

	var err error
	// set browser default as chrome
	const browserENV = "BROWSER"
	browserName := os.Getenv(browserENV)
	if browserName == "" {
		browserName = "chrome"
	}
	caps := selenium.Capabilities(map[string]interface{}{"browserName": browserName})

	// remote to selenium server
	if driver, err = selenium.NewRemote(caps, ""); err != nil {
		panic(err)
		return
	}

	const credentials = "jdoe:password"
	const swsURLENV = "SWS_URL"
	swsURL := os.Getenv(swsURLENV)
	if swsURL == "" {
		panic(fmt.Sprintf("Environment variable %s should be set.", swsURLENV))
	}
	var swsUIURL = fmt.Sprintf("http://%s@%s/console/", credentials, swsURL)

	page = pages.Page{Driver: driver}
	err = driver.Get(swsUIURL)
	if err != nil {
		fmt.Printf("Failed to load page: %s\n", err)
		panic(err)
		return
	}

	const titleXpath = "//h1[@class='App-title']"
	sel := page.FindElementByXpath(titleXpath)

	titleUI, err := sel.Text()

	if err != nil {
		panic(err)
	}

	assert.Equal(t, titleUI, "Welcome to React")

	var restURL = fmt.Sprintf("http://%s@%s/api/", credentials, swsURL)

	resty.SetRedirectPolicy(resty.FlexibleRedirectPolicy(20))
	resp, err := resty.R().Get(restURL)

	if err != nil {
		panic(err)
	}

	assert.Equal(t, resp.String(), "Welcome to SWS API Server!")

	driver.Quit()
}
