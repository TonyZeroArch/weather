Feature: Weather Dashboard Invalid City Search
  A user should see an error if they search for a city that does not exist.

  Scenario: User searches for an invalid city
    Given I open the weather dashboard
    When I enter "FakeCity123" into the city search field
    And I click the "Search" button
    Then I should see an error message "City not found"