Feature: Weather Dashboard Search

  Scenario: User searches for the weather in a valid city
    Given I open the weather dashboard
    When I enter "New York" into the city search field
    And I click the "Search" button
    Then I should see the current weather for "New York"