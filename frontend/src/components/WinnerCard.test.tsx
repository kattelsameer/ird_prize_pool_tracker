import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import { WinnerCard } from "./WinnerCard";
import { renderWithProviders } from "../test/testUtils";
import { fixtureMatches } from "../test/fixtures";

describe("WinnerCard", () => {
  it("shows all three data-source labels (government, user, app) plus the claim disclaimer", () => {
    renderWithProviders(<WinnerCard match={fixtureMatches[0]} />);

    expect(screen.getByText(/IRD published data/i)).toBeInTheDocument();
    expect(screen.getByText(/Your entry/i)).toBeInTheDocument();
    expect(screen.getByText(/App-calculated/i)).toBeInTheDocument();

    // Never implies a guaranteed prize.
    expect(screen.getByText(/does not guarantee payment/i)).toBeInTheDocument();
    expect(screen.getByText(/original physical bill/i)).toBeInTheDocument();
  });

  it("shows a fiscal-year-unconfirmed notice when applicable", () => {
    const unconfirmedMatch = { ...fixtureMatches[0], fiscal_year_unconfirmed: true };
    renderWithProviders(<WinnerCard match={unconfirmedMatch} />);
    expect(screen.getByRole("note")).toHaveTextContent(/haven't confirmed a fiscal year/i);
  });
});
